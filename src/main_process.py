import pandas as pd
import logging

from pathlib import Path
from datetime import datetime

from config.config import Config
from src.dataprocess.DataProcess import DataRead
from src.report.GPT import GPT
from src.report.RoutingDelay import RoutingDelay
from src.report.TransportationDelay import TransportationDelay
from src.report.InboundInventory import InboundInventory
from src.report.OutboundInventory import OutboundInventory
from src.report.SubmissionDelay import SubmissionDelay
from src.report.DispatchDelay import DispatchDelay


class MainProcess():
    """该项目的主流程逻辑
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def run(self) -> None:
        """主运行方法
        """
        
        self.logger.info("-"*50)
        self.logger.info("报表制作流程-开始.")
        
        dataread: DataRead = DataRead()
        report_path: dict[str, list[Path]] = dataread.run()
        
        # GPT报表
        Gpt: GPT = GPT(report_path['gpt'])
        gpt: pd.DataFrame = Gpt.run()
        
        # 路由延误报表
        routingdelay: RoutingDelay = RoutingDelay(gpt, report_path['routing'])
        routing: pd.DataFrame = routingdelay.run()
        
        # 干线运输延误报表
        transportationdelay: TransportationDelay = TransportationDelay(gpt, report_path['transportation'])
        transportation: pd.DataFrame = transportationdelay.run()
        
        # 进港超时库存报表
        inboundinventory: InboundInventory = InboundInventory(gpt, report_path['inbound'])
        inbound: pd.DataFrame = inboundinventory.run()
        
        # 出港超时库存报表
        outboundinventory: OutboundInventory = OutboundInventory(gpt, report_path['outbound'])
        outbound: pd.DataFrame = outboundinventory.run()
        
        # 交件延误报表
        submissiondelay: SubmissionDelay = SubmissionDelay(gpt, report_path['submission'])
        submission: pd.DataFrame = submissiondelay.run()
        
        # 派签延误报表
        dispatchdelay: DispatchDelay = DispatchDelay(gpt, report_path['dispatch'])
        dispatch: pd.DataFrame = dispatchdelay.run()
        
        file = rf"C:\Users\admin\Desktop\{datetime.now(): %m-%d}淘天线路时效GTP数据.xlsx"
        
        with pd.ExcelWriter(file, engine="openpyxl", mode="w") as writer:
            # GPT
            gpt_cols: list[str] = list(gpt.columns)
            for col in gpt_cols:
                if "占比" in col:
                    gpt[col] = gpt[col].apply(lambda x: f"{x: .2%}")
            gpt.to_excel(writer, sheet_name="GPT", index=False)
            # 路由
            routing.to_excel(writer, sheet_name="路由", index=False)
            # 运输
            transportation.to_excel(writer, sheet_name="运输", index=False)
            # 交件
            submission.to_excel(writer, sheet_name="交件", index=False)
            # 派签
            dispatch.to_excel(writer, sheet_name="派签", index=False)
            # 中心库存
            center:pd.DataFrame = pd.concat([outbound, inbound], axis=0, ignore_index=True)
            center.to_excel(writer, sheet_name="中心库存", index=False)
        
        
        
        self.logger.info("报表制作流程-结束.")
        self.logger.info("-"*50)