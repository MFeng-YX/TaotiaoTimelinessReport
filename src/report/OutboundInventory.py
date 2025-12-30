import pandas as pd
import logging

from pathlib import Path

from config.config import Config


class OutboundInventory():
    """制作进港库存报表
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self, gpt: pd.DataFrame, path: list[Path]):
        """初始化 OutboundInventory 类实例

        Args:
            gpt (pd.DataFrame): _description_
            path (list[Path]): _description_
        """
        
        self.gpt = gpt
        self.outbound = self.config.outbound
        self.path = path
        
        
    def data_read(self) -> list[pd.DataFrame]:
        """读取制作报表需要的表格数据

        Returns:
            list[pd.DataFrame]: 表格数据列表
        """
        
        for p in self.path:
            if "出港环节" in p.name:
                details = pd.read_excel(p)
            
            if "超时库存" in p.name:
                inventory = pd.read_excel(p)
            
            if "城市对应中心" in p.name:
                center = pd.read_excel(p)
        
        details = details.loc[:, self.outbound['出港汇总']].copy()
        inventory = inventory.loc[:, self.outbound["出港超时库存"]].copy()
        center = center.loc[:, self.outbound['城市对应中心']].copy()
        
        self.logger.info("OutboundInventory 报表需要的数据读取完成.")
        
        return [details, inventory, center]
    
    
    def report_production(self, df_list: list[pd.DataFrame]) -> pd.DataFrame:
        """制作 OutboundInventory 报表

        Args:
            df_list (list[pd.DataFrame]): 制作报表需要的文件数据

        Returns:
            pd.DataFrame: 报表
        """
        
        details, inventory, center = df_list
        
        route_need = self.gpt[self.gpt["中心出港操作占比"] > 0.05]['城市线路']
        details = details.loc[details['城市线路名称'].isin(route_need)].copy()
        details = details.rename(columns={"揽收城市名称": "城市"})
        details = details.merge(center, how="left", on="城市")
        details_group = (details
                         .groupby("发货中心")['出港超时库存']
                         .sum()
                         .reset_index()
                         .rename(columns={"发货中心": "责任中心", "出港超时库存": "线路延误量"}))
        inventory = inventory.rename(columns={
                                    "中心名称": "责任中心", 
                                    "发车超时库存票数": "相应期间中心延误量",
                                    "超时库存占比": "库存比例"
                                    })
        outbound = details_group.merge(inventory, how="left", on="责任中心")
        outbound['类型'] = "出港库存"
        cols = list( outbound.columns)
        cols.insert(0, cols.pop(cols.index("类型")))
        outbound =  outbound.loc[:, cols]
        
        outbound['库存比例'] = outbound["库存比例"].apply(lambda x: f"{x: .2f}%")
        
        new_row = pd.DataFrame([{"类型": "出港库存-汇总", "线路延误量": outbound['线路延误量'].sum()}])
        outbound = pd.concat([ outbound, new_row], ignore_index=True)
        
        self.logger.info("OutboundInventory 报表制作完成.")
        
        return outbound
    
    
    def run(self) -> pd.DataFrame:
        """该类的主运行方法

        Returns:
            pd.DataFrame: OutboundInventory 报表
        """
        
        self.logger.info("-"*50)
        self.logger.info("OutboundInventory报表制作流程-开始.")
        
        df_list = self.data_read()
        outbound: pd.DataFrame = self.report_production(df_list)
        
        self.logger.info("OutboundInventory报表制作流程-结束.")
        self.logger.info("-"*50)
        
        return outbound