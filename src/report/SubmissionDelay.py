import pandas as pd
import logging

from pathlib import Path

from config.config import Config

# 城市线路名称需要进行排序

class SubmissionDelay():
    """制作交件延误报表
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self, gpt: pd.DataFrame, path: list[Path]):
        """初始化 SubmissionDelay 类实例

        Args:
            gpt (pd.DataFrame): GPT报表
            path (list[Path]): SubmissionDelay报表需要的表格路径
        """
        
        self.gpt = gpt
        self.submission = self.config.submission
        self.path = path
        
        
    def data_read(self) -> pd.DataFrame:
        """读取制作报表需要的文件数据

        Returns:
            list[pd.DataFrame]: 数据列表
        """
        
        path = self.path[0]
        
        details = pd.read_excel(path)
        details = details.loc[:, self.submission['交件']].rename(columns={"交件延误量": "延误量"})
        
        self.logger.info("SubmissionDelay 报表需要的数据读取完成")
        
        return details
    
    
    def report_production(self, details: pd.DataFrame) -> pd.DataFrame:
        """制作 SubmissionDelay 报表

        Args:
            details (pd.DataFrame): 制作报表需要的数据

        Returns:
            pd.DataFrame: 报表
        """
        
        route_need = self.gpt[self.gpt['网点交件占比'] > 0.05]['城市线路']
        details = details.loc[details['城市线路名称'].isin(route_need), :].copy()
        df = details.groupby("城市线路名称")['延误量'].sum().rename("Top5网点延误量总计").reset_index()
        submission = details.merge(df, how="left", on="城市线路名称")
        submission = submission.sort_values(by="城市线路名称")
        
        cols = list(submission.columns)
        cols.insert(1, cols.pop(cols.index("Top5网点延误量总计")))
        submission = submission.loc[:, cols]
        
        self.logger.info("SubmissionDelay 报表制作完成")
        
        return submission
    
    
    def run(self) -> pd.DataFrame:
        """该类的主运行方法

        Returns:
            pd.DataFrame: SubmissionDelay 报表
        """
        
        self.logger.info("-"*50)
        self.logger.info("SubmissionDelay报表制作流程-开始.")
        
        df_list = self.data_read()
        submission: pd.DataFrame = self.report_production(df_list)
        
        self.logger.info("SubmissionDelay报表制作流程-结束.")
        self.logger.info("-"*50)
        
        return submission