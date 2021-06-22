# encoding='utf-8'

import logging

logger = logging.getLogger(__name__)
logging.root.setLevel(logging.DEBUG)
logFormat = logging.Formatter('%(asctime)s %(filename)s:%(lineno)s %(funcName)s %(levelname)s %(message)s')

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(logFormat)
logger.addHandler(sh)

# th = handlers.TimedRotatingFileHandler(filename='new.log',when='D',backupCount=3,encoding='utf-8')
fh = logging.FileHandler('new.log', mode='w', encoding='utf-8')
fh.setLevel(logging.ERROR)
fh.setFormatter(logFormat)
logger.addHandler(fh)

logger.debug("苍井空")
logger.info("麻生希")
logger.warning("小泽玛利亚")
logger.error("桃谷绘里香")
logger.critical("泷泽萝拉")