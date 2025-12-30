import logging

from pathlib import Path
from config.config import Config

class DataRead():
    """读取文件路径
    """
    
    config: Config = Config.from_json()
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    def __init__(self):
        """初始化 DataRead 类实例
        """
        
        self.dir_path: str = self.config.datapath
        
    
    def path_read(self) -> list[Path]:
        """读取data文件夹中的文件路径

        Returns:
            list[Path]: 文件路径列表
        """
        
        dir_path: Path = Path(self.dir_path)
        
        path_list: list[Path] = list()
        for f in dir_path.rglob("*淘天平台线路时效分析*.xlsx"):
            path_list.append(f)
            
        for f in dir_path.rglob("*线路达成率*.xlsx"):
            path_list.append(f)
            
        for f in dir_path.rglob("*线路罚款*.csv"):
            path_list.append(f)
        
        for f in dir_path.rglob("*超时库存*.xlsx"):
            path_list.append(f)
        
        path: Path = Path("./config/城市对应中心基础表1119.xlsx")
        path_list.append(path)
            
        self.logger.info(f"路径读取完成, 一共读取到 {len(path_list)} 个文件路径.")
            
        return path_list
    
    
    def path_label(self, path_list: list[Path]) -> dict[str, list[Path]]:
        """对文件进行类别标记

        Args:
            path_list (list[Path]): 文件路径列表

        Returns:
            dict[str, list[Path]]: 类别对应路径字典
        """
        
        report_path: dict[str, list[Path]] = dict()
        report_path['gpt'] = list()
        report_path['inbound'] = list()
        report_path['outbound'] = list()
        report_path['routing'] = list()
        report_path['transportation'] = list()
                       
        for p in path_list:              
            if "各环节延误量" in p.name:
                report_path['gpt'].append(p)
                
            if "城市线路汇总-日" in p.name:
                report_path['gpt'].append(p)
                
            if "未达成车签明细" in p.name or "线路罚款" in p.name:
                report_path['routing'].append(p)
                report_path['transportation'].append(p)
            
            if "进港" in p.name or "城市对应中心" in p.name:
                report_path['inbound'].append(p)
            
            if "出港" in p.name or "城市对应中心" in p.name:
                report_path['outbound'].append(p)
                
            if "交件" in p.name:
                report_path['submission'] = [p]
                
            if '派签' in p.name:
                report_path['dispatch'] = [p]
                
        self.logger.info("文件路径类别标记完成.")
                
        return report_path
    
    
    def run(self) -> dict[str, list[Path]]:
        """DataRead类的主运行方法

        Returns:
            dict[str, list[Path]]: 类别对应路径字典
        """
        self.logger.info("-"*50)
        self.logger.info("文件路径读取流程-开始")
        
        path_list = self.path_read()
        report_path = self.path_label(path_list)
        
        self.logger.info("文件路径读取流程-结束")
        self.logger.info("-"*50)
        
        return report_path