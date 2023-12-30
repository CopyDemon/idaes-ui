from typing import Optional


class InitialParams:
    """This class use to populate all params use in "self" (main_class) in the main.
    Args:
        main_class: the class instence called this class
        flowsheet: flowsheet
        name: flowsheet name
        port: Optional, port for uvicorn serve web default 8000
        save_time_interval: Optional, the duration time will send to front end to call api/put_fs to update flowsheet, default 5s
        save_dir: Optional, dir use to store user saved flowsheet, default "./saved_flowsheet"
    """

    def __init__(
        self,
        main_class,
        flowsheet,
        name,
        port: Optional[int] = None,
        save_time_interval: Optional[int] = 5,
        save_dir: Optional[str] = None,
    ):
        # initial everything related to flowsheet
        main_class.flowsheet = flowsheet
        main_class.flowsheet_name = name

        # populate web port
        if port is not None:
            main_class.port = port
        else:
            main_class.port = 8000

        # initial save_time_interval
        main_class.save_time_interval = save_time_interval

        # initial save dir
        if save_dir:
            main_class.save_dir = save_dir
        else:
            main_class.save_dir = "./saved_flowsheet"
