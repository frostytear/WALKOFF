import logging

import walkoff.config.config
from walkoff.core.multiprocessedexecutor.multiprocessedexecutor import MultiprocessedExecutor
from walkoff.core.scheduler import Scheduler
import walkoff.coredb.devicedb
from walkoff.coredb.workflow import Workflow

logger = logging.getLogger(__name__)

WORKFLOW_RUNNING = 1
WORKFLOW_PAUSED = 2
WORKFLOW_COMPLETED = 4

NUM_PROCESSES = walkoff.config.config.num_processes


class Controller(object):
    def __init__(self, executor=MultiprocessedExecutor):
        """Initializes a Controller object.
        
        Args:
            executor (cls, optional): The executor to use in the controller. Defaults to MultiprocessedExecutor
        """
        self.id = 'controller'
        self.scheduler = Scheduler()
        self.executor = executor()

    def initialize_threading(self, pids=None):
        """Initializes threading in the executor
        """
        self.executor.initialize_threading(pids=pids)

    def wait_and_reset(self, num_workflows):
        """Waits for the specified number of workflows to finish execution.

        Args:
            num_workflows (int): The number of workflows to wait for.
        """
        self.executor.wait_and_reset(num_workflows)

    def shutdown_pool(self):
        """Shuts down the executor
        """
        self.executor.shutdown_pool()

    def pause_workflow(self, execution_uid):
        """Pauses a workflow.

        Args:
            execution_uid (str): The execution UID of the workflow to pause
        """

        return self.executor.pause_workflow(execution_uid)

    def resume_workflow(self, workflow_execution_uid):
        """Resumes a workflow that has been paused.

        Args:
            workflow_execution_uid (str): The randomly-generated hexadecimal key that was returned from
                pause_workflow(). This is needed to resume a workflow for security purposes.

        Returns:
            (bool) True if successful, False otherwise.
        """
        return self.executor.resume_workflow(workflow_execution_uid)

    def schedule_workflows(self, task_id, workflow_ids, trigger):
        """Schedules workflows to be run by the scheduler

        Args:
            task_id (str|int): Id of the task to run
            workflow_ids (list[int]): IDs of the workflows to schedule
            trigger: The type of scheduler trigger to use
        """
        self.scheduler.schedule_workflows(task_id, self.execute_workflow, workflow_ids, trigger)

    def execute_workflow(self, workflow_id, start=None, start_arguments=None, resume=False):
        """Executes a workflow.

        Args:
            workflow_id (int): ID of the workflow to execute.
            start (int, optional): The ID of the first, or starting action. Defaults to None.
            start_arguments (list[Argument]): The input to the starting action of the workflow. Defaults to None.
            resume (bool, optional): Optional boolean to resume a previously paused workflow. Defaults to False.

        Returns:
            The execution UID if successful, None otherwise.
        """
        workflow = walkoff.coredb.devicedb.device_db.session.query(Workflow).filter_by(id=workflow_id).first()
        if workflow:
            return self.executor.execute_workflow(workflow, start, start_arguments, resume)
        else:
            logger.error('Attempted to execute playbook which does not exist')
            return None, 'Attempted to execute playbook which does not exist'

    def get_waiting_workflows(self):
        return self.executor.get_waiting_workflows()

    def get_workflow_status(self, execution_uid):
        """Gets the status of an executing workflow

        Args:
            execution_uid (str): Execution UID of the executing workflow

        Returns:
            (int) Status code of the executing workflow
        """
        return self.executor.get_workflow_status(execution_uid)


controller = Controller()