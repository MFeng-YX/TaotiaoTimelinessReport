import pandas as pd
import logging

from pathlib import Path

from config.config import Config

# 要加3列数据： 标准时效、与第一差值、达成率，加在城市线路后面


class RoutingDelay():
    """路由延误报表制作
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self, gpt: pd.DataFrame, path: list[Path]):
        """初始化 RoutingDelay类实例

        Args:
            gpt (pd.DataFrame): GPT报表
            path(list[Path]): 报表需要的表格路径
        """
        
        self.gpt: pd.DataFrame = gpt
        self.routing: dict[str, list[str]] = self.config.routing
        self.path: list[Path] = path
        
        
    def data_read(self) -> list[pd.DataFrame]:
        """读取报表制作需要的数据

        Returns:
            list[pd.DataFrame]: 需要的报表数据
        """    
             
        for p in self.path:
            if "未达成车签明细" in p.name:
                details: pd.DataFrame = pd.read_excel(p)
            
            if "线路罚款" in p.name:
                center: pd.DataFrame = pd.read_excel(p, skiprows=[0])                  
        
        details = details.loc[details[self.routing['筛选'][0]] == "是", self.routing["未达成车签明细"]].copy()
        
        center = center.loc[:, self.routing['线路罚款']]
        
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
        
        route_need = self.gpt[self.gpt['路由占比'] > 0.05]['城市线路']
        details = details.loc[details['城市到城市线路名称'].isin(route_need), self.routing['未达成车签明细']].copy()
        details = details.rename(columns={'城市到城市线路名称': '城市线路', "最晚发车时间": "建议发车时间", "未达成量": "线路延误量"})
        details = details.loc[details['线路延误量'] > 100, :].copy()
        details['建议发车时间'] = pd.to_datetime(details['建议发车时间'], format="mixed", errors="coerce")
        details['建议网点交件时间'] = (details['建议发车时间'] - pd.Timedelta(hours=1)).dt.strftime('%H:%M:%S')
        df = pd.merge(
            details, center,
            how="left",
            left_on="车签", right_on="电子车签"
        ).rename(columns={"线路名称": "中心线路"})
        gpt_need = self.gpt.loc[:, ["城市线路", "标准时效", "与第一差值(%)", "达成率(%)",]]
        df = df.merge(gpt_need, how="left", on="城市线路")
        
        if not set(self.routing['列顺序']) - set(df.columns):
            self.logger.info("RoutingDelay报表制作完成.")
            return df.loc[:, self.routing['列顺序']]
        else:
            self.logger.error("输出报表中的列名与所需求的不一致,请检查逻辑")
            self.logger.info(f"报表中的列名为: {list(df.columns)}")
            raise ValueError("输出报表中的列名与所需求的不一致,请检查逻辑")
    
    
    def run(self) -> pd.DataFrame:
        """RoutingDelay 类的主运行方法

        Returns:
            pd.DataFrame: RoutingDelay报表
        """
        
        self.logger.info("-"*50)
        self.logger.info("RoutingDelay报表制作流程-开始.")
        
        df_list = self.data_read()
        routing: pd.DataFrame = self.report_production(df_list)
        
        self.logger.info("RoutingDelay报表制作流程-结束.")
        self.logger.info("-"*50)
        
        return routing