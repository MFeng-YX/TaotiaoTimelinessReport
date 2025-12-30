import pandas as pd
import logging

from pathlib import Path

from config.config import Config


class TransportationDelay():
    """干线运输延误报表制作
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self, gpt: pd.DataFrame, path: list[Path]):
        """初始化 TransportationDelay 类实例

        Args:
            gpt (pd.DataFrame): GPT报表
            path (list[Path]): 报表需要的表格路径
        """
        
        self.gpt = gpt
        self.transportation = self.config.transportation
        self.path = path
        
    
    def data_read(self) -> list[pd.DataFrame]:
        """读取需要的文件数据

        Returns:
            list[pd.DataFrame]: 读取到的表格数据列表
        """

        for p in self.path:
            if "未达成车签明细" in p.name:
                details: pd.DataFrame = pd.read_excel(p)
            
            if "线路罚款" in p.name:
                center: pd.DataFrame = pd.read_excel(p, skiprows=[0])
        
        details_col_need = self.transportation["未达成车签明细"] 
        details = details.loc[details[self.transportation['筛选'][0]] == "是", details_col_need].copy()
        
        center = center.loc[:, self.transportation['线路罚款']]
        
        self.logger.info("数据读取完成.")
        
        return [details, center]
    
    
    def report_production(self, df_list: list[pd.DataFrame]) -> pd.DataFrame:
        """ 制作 RoutingDelay 报表

        Args:
            df_list (list[pd.DataFrame]): 制作报表需要的数据

        Returns:
            pd.DataFrame: RoutingDelay 报表
        """
        
        details, center = df_list
        
        center = center.rename(columns={"电子车签": "车签"})
        
        route_need = self.gpt[self.gpt['干线运输占比'] > 0.05]['城市线路']
        details = details.loc[details['城市到城市线路名称'].isin(route_need), self.transportation['未达成车签明细']].copy()
        details = details.rename(columns={'城市到城市线路名称': '城市线路', "未达成量": "线路延误量"})
        details = details.loc[details['线路延误量'] > 10, :].copy()
        df: pd.DataFrame = details.merge(
            center,
            how="left",
            on="车签"
        ).rename(columns={"线路名称": "中心线路"})
        
        cols = list(df.columns)
        cols.insert(1, cols.pop(cols.index("中心线路")))
        transportation = df.loc[:, cols]
        transportation = transportation.sort_values(by="城市线路")
        
        self.logger.info("TransportationDelay 报表制作完成.")
        
        return transportation
    
    
    def run(self) -> pd.DataFrame:
        """该类的主运行方法

        Returns:
            pd.DataFrame: TransportationDelay报表
        """
        
        self.logger.info("-"*50)
        self.logger.info("TransportationDelay报表制作流程-开始.")
        
        df_list = self.data_read()
        transportation: pd.DataFrame = self.report_production(df_list)
        
        self.logger.info("TransportationDelay报表制作流程-结束.")
        self.logger.info("-"*50)
        
        return transportation