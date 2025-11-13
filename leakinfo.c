#define LEAK_POS __LEAK_Pos
#define NUMBER_ONLY __NUMBER_Only
// #define LEAK_POS 0
// #define NUMBER_ONLY 0
#define LEAK_WA_ANS "__PTA_TestInput_Spy__"

#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
// #include <sys/utsname.h>
#include <sys/stat.h>
#include <unistd.h>

#include <sys/syscall.h>
#include <errno.h>
#define BPF_MAP_CREATE 0

typedef struct String {
    char* str;
    size_t len, volume;
} String;

String* String_New() {
    String* s = (String*)malloc(sizeof(String));
    s->len = 0;
    s->volume = 8;
    s->str = (char*)calloc(s->volume, sizeof(char));
    return s;
}

void String_Expand(String* s, size_t toLen) {
    while (s->volume <= toLen) {
        s->volume <<= 1;
    }
    char* nSpace = (char*)calloc(s->volume, sizeof(char));
    memcpy(nSpace, s->str, s->len);
    free(s->str);
    s->str = nSpace;
}

String* String_Append(String* s, const char* sApp) {
    if (!s || !sApp) {
        return s;
    }
    
    size_t sAppLen = strlen(sApp);
    size_t nLen = s->len + sAppLen;
    if (nLen + 1 >= s->volume) {
        String_Expand(s, nLen + 1);
    }
    strcat(s->str, sApp);
    s->len = nLen;
    return s;
}

void String_Delete(String* s) {
    free(s->str);
    free(s);
}

extern char **environ;

int main(void) {
    String* s = String_New();

    // struct utsname info;
    // if (uname(&info) == -1) {
    //     return 250;
    // }

    // String_Append(s, info.sysname);
    // String_Append(s, ";");
    // String_Append(s, info.nodename);
    // String_Append(s, ";");
    // String_Append(s, info.release);
    // String_Append(s, ";");
    // String_Append(s, info.version);
    // String_Append(s, ";");
    // String_Append(s, info.machine);
    // uid_t uid = getuid();
    // char buf[64] = {0};
    // sprintf(buf, "%d", uid);
    // String_Append(s, buf);

    // char buf[256] = {0};
    // FILE* fp = fopen("a.c", "r");
    // while (fgets(buf, sizeof(buf), fp)) {
    //     String_Append(s, buf);
    // }

    // DIR* dir = opendir("../lib64");
    // struct dirent *entry;
    // while ((entry = readdir(dir)) != NULL) {
    //     if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
    //         continue;

    //     String_Append(s, entry->d_name);
    //     String_Append(s, ";");
    // }

    // for (char **env = environ; *env != NULL; env++) {
    //     String_Append(s, *env);
    //     String_Append(s, "\n");
    // }

    int ret = syscall(__NR_bpf, BPF_MAP_CREATE, 0, 0);
    if (ret == -1) {
        if (errno == EPERM) {
            String_Append(s, "NoPermission");
        } else if (errno == EACCES) {
            String_Append(s, "Blocked");
        } else if (errno == EINVAL) {
            String_Append(s, "eBPF OK!");
        } else {
            char buf[64] = {0};
            sprintf(buf, "Errno: %d", errno);
            String_Append(s, buf);
        }
    }
    
    if (LEAK_POS > s->len) {
        puts(LEAK_WA_ANS);
        return 0;
    }

    char ch = s->str[LEAK_POS];
    String_Delete(s);
    return ch;
}
