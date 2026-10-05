import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from config.env import AppConfig
class FutureIntradayService:
 @classmethod
 def get(cls,thscode):
  load_dotenv(Path(AppConfig.future_stat_db_path).parent/'.env');key=os.getenv('HITHINK_FINANCE_API_KEY') or os.getenv('FUYAO_API_KEY')
  r=requests.get('https://fuyao.aicubes.cn/api/futures/prices/intraday',params={'thscode':thscode,'session':'intraday'},headers={'X-api-key':key},timeout=(5,20));r.raise_for_status();p=r.json()
  if int(p.get('code',-1))!=0:raise RuntimeError(p.get('message'))
  return p.get('data') or {}
