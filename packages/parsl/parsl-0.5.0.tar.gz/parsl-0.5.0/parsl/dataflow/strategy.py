import logging
import time
import math

logger = logging.getLogger(__name__)


class Strategy (object):
    """FlowControl Strategy.

    As a workflow dag is processed by Parsl, new tasks are added and completed
    asynchronously. Parsl interfaces executors with execution providers to construct
    scalable execution sites to handle the variable work-load generated by the
    workflow. This component is responsible for periodically checking outstanding
    tasks and available compute capacity and trigger scaling events to match
    workflow needs.

    Here's a diagram of a site. A site consists of blocks, which are usually
    created by single requests to a Local Resource Manager (LRM) such as slurm,
    condor, torque, or even AWS API. The blocks could contain several task blocks
    which are separate instances on workers.


    .. code:: python

                |<--minBlocks     |<-initBlocks              maxBlocks-->|
                +--------------------------------------------------------+
                |  +--------Block--------+       +--------Block--------+ |
         Site = |  | TaskBlock TaskBlock | ...   | TaskBlock TaskBlock | |
                |  +---------------------+       +---------------------+ |
                +--------------------------------------------------------+

    The general shape and bounds of a site are user specified through:

       1. minBlocks: Minimum number of blocks to maintain per site
       2. initBlocks: number of blocks to provision at initialization of workflow
       3. maxBlocks: Maximum number of blocks that can be active at a site from one workflow.


    .. code:: python

          slots = current_capacity * taskBlocks

          active_tasks = pending_tasks + running_tasks

          Parallelism = slots / tasks
                      = [0, 1] (i.e,  0 <= p <= 1)

    For example:

    When p = 0,
         => compute with the least resources possible.
         infinite tasks are stacked per slot.

         .. code:: python

               blocks =  minBlocks           { if active_tasks = 0
                         max(minBlocks, 1)   {  else

    When p = 1,
         => compute with the most resources.
         one task is stacked per slot.

         .. code:: python

               blocks = min ( maxBlocks,
                        ceil( active_tasks / slots ) )


    When p = 1/2,
         => We stack upto 2 tasks per slot before we overflow
         and request a new block


    let's say min:init:max = 0:0:4 and taskBlocks=2

    In the diagram, X <- task

    at 2 tasks :

    .. code:: python

        +---Block---|
        |           |
        | X      X  |
        |slot   slot|
        +-----------+

    at 5 tasks, we overflow as the capacity of a single block is fully used.

    .. code:: python

        +---Block---|       +---Block---|
        | X      X  | ----> |           |
        | X      X  |       | X         |
        |slot   slot|       |slot   slot|
        +-----------+       +-----------+

    """

    def __init__(self, dfk):
        """Initialize strategy."""
        self.dfk = dfk
        self.config = dfk.config
        self.sites = {}
        self.max_idletime = 60 * 2  # 2 minutes

        for site in self.dfk.config["sites"]:
            self.sites[site['site']] = {'idle_since': None,
                                        'config': site}

        self.strategies = {None: self._strategy_noop,
                           'simple': self._strategy_simple}

        strtgy_name = self.config['globals'].get('strategy', None)
        self.strategize = self.strategies.get(strtgy_name,
                                              self._strategy_noop)

        logger.debug("Scaling strategy: {0}".format(strtgy_name))

    def _strategy_noop(self, tasks, *args, kind=None, **kwargs):
        """Do nothing.

        Args:
            - tasks (task_ids): Not used here.

        KWargs:
            - kind (Not used)
        """

    def _strategy_simple(self, tasks, *args, kind=None, **kwargs):
        """Peek at the DFK and the sites specified.

        We assume here that tasks are not held in a runnable
        state, and that all tasks from an app would be sent to
        a single specific site, i.e tasks cannot be specified
        to go to one of more sites.

        Args:
            - tasks (task_ids): Not used here.

        KWargs:
            - kind (Not used)
        """
        # Add logic to check sites
        # for task in tasks :
        #    if self.dfk.tasks[task]:

        for sitename in self.dfk.executors:

            exc = self.dfk.executors[sitename]
            site_config = self.sites[sitename]['config']

            if not exc.scaling_enabled:
                logger.debug("Site:{0} Status:STATIC".format(sitename))
                continue

            # Tasks that are either pending completion
            active_tasks = exc.executor.outstanding

            # Get the status of the taskBlocks
            status = exc.status()

            # Get the shape and bounds for the site
            minBlocks = site_config["execution"]["block"]["minBlocks"]
            maxBlocks = site_config["execution"]["block"]["maxBlocks"]
            initBlocks = site_config["execution"]["block"]["initBlocks"]
            taskBlocks = site_config["execution"]["block"]["taskBlocks"]
            parallelism = site_config["execution"]["block"]["parallelism"]

            active_blocks = sum([1 for x in status if x in ('RUNNING',
                                                            'SUBMITTING',
                                                            'PENDING')])
            active_slots = active_blocks * taskBlocks

            logger.debug("Min:{} initBlocks:{} Max:{}".format(minBlocks,
                                                              initBlocks,
                                                              maxBlocks))
            # import pdb; pdb.set_trace()
            logger.debug("Tasks:{} Slots:{} Parallelism:{}".format(len(active_tasks),
                                                                   active_slots,
                                                                   parallelism))

            # Case 1
            # No tasks.
            if len(active_tasks) == 0:
                # Case 1a
                # Fewer blocks that minBlocks
                if active_blocks <= minBlocks:
                    # Ignore
                    # logger.debug("Strategy: Case.1a")
                    pass

                # Case 1b
                # More blocks than minBlocks. Scale down
                else:
                    # We want to make sure that max_idletime is reached
                    # before killing off resources
                    if not self.sites[sitename]['idle_since']:
                        logger.debug("Strategy: Scale_in, tasks=0 starting kill timer")
                        self.sites[sitename]['idle_since'] = time.time()

                    idle_since = self.sites[sitename]['idle_since']
                    if (time.time() - idle_since) > self.max_idletime:
                        # We have resources idle for the max duration,
                        # we have to scale_in now.
                        logger.debug("Strategy: Scale_in, tasks=0")
                        exc.scale_in(active_blocks - minBlocks)

                    else:
                        pass
                        # logger.debug("Strategy: Case.1b. Waiting for timer : {0}".format(idle_since))

            # Case 2
            # More tasks than the available slots.
            elif (float(active_slots) / len(active_tasks)) < parallelism:
                # Case 2a
                # We have the max blocks possible
                if active_blocks >= maxBlocks:
                    # Ignore since we already have the max nodes
                    # logger.debug("Strategy: Case.2a")
                    pass

                # Case 2b
                else:
                    # logger.debug("Strategy: Case.2b")
                    excess = math.ceil((len(active_tasks) * parallelism) - active_slots)
                    excess_blocks = math.ceil(float(excess) / taskBlocks)
                    logger.debug("Requesting {} more blocks".format(excess_blocks))
                    exc.scale_out(excess_blocks)

            elif active_slots == 0 and len(active_tasks) > 0:
                # Case 4
                # Check if slots are being lost quickly ?
                logger.debug("Requesting single slot")
                exc.scale_out(1)
            # Case 3
            # tasks ~ slots
            else:
                # logger.debug("Strategy: Case 3")
                pass


if __name__ == '__main__':

    pass
