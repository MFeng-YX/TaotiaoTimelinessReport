import pandas as pd
import logging

from pathlib import Path

from config.config import Config


import pandas as pd
import logging

from pathlib import Path

from config.config import Config

# 城市线路名称需要进行排序

class DispatchDelay():
    """制作派签延误报表
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self, gpt: pd.DataFrame, path: list[Path]):
        """初始化 DispatchDelay 类实例

        Args:
            gpt (pd.DataFrame): GPT报表
            path (list[Path]): DispatchDelay报表需要的表格路径
        """
        
        self.gpt = gpt
        self.dispatch = self.config.dispatch
        self.path = path
        
        
    def data_read(self) -> pd.DataFrame:
        """读取制作报表需要的文件数据

        Returns:
            list[pd.DataFrame]: 数据列表
        """
        
        path = self.path[0]
        
        details = pd.read_excel(path)
        details = details.loc[:, self.dispatch['派签']]
        
        self.logger.info("DispatchDelay 报表需要的数据读取完成")
        
        return details
    
    
    def report_production(self, details: pd.DataFrame) -> pd.DataFrame:
        """制作 DispatchDelay 报表

        Args:
            details (pd.DataFrame): 制作报表需要的数据

        Returns:
            pd.DataFrame: 报表
        """
        
        route_need = self.gpt['城市线路']
        details = details.loc[details['城市线路名称'].isin(route_need), :].copy()
        df = details.groupby("城市线路名称")['延误量'].sum().rename("Top5网点延误量总计").reset_index()
        dispatch = details.merge(df, how="left", on="城市线路名称")
        dispatch = dispatch.sort_values(by="城市线路名称")
        
        cols = list(dispatch.columns)
        cols.insert(1, cols.pop(cols.index("Top5网点延误量总计")))
        dispatch = dispatch.loc[:, cols]
        
        self.logger.info("DispatchDelay 报表制作完成")
        
        return dispatch
    
    
    def run(self) -> pd.DataFrame:
        """该类的主运行方法

        Returns:
            pd.DataFrame: DispatchDelay 报表
        """
        
        self.logger.info("-"*50)
        self.logger.info("DispatchDelay报表制作流程-开始.")
        
        df_list = self.data_read()
        dispatch: pd.DataFrame = self.report_production(df_list)
        
        self.logger.info("DispatchDelay报表制作流程-结束.")
        self.logger.info("-"*50)
        
        return dispatch