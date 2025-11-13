// #define LEAK_POS __LEAK_Pos
// #define NUMBER_ONLY __NUMBER_Only
#define LEAK_POS 0
#define NUMBER_ONLY 0
#define LEAK_WA_ANS "__PTA_TestInput_Spy__"

#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <sys/stat.h>

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

int main(void) {
    DIR *dir = opendir(".");
    if (!dir) {
        perror("CannotOpen");
        return 1;
    }

    String* s = String_New();
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, ".."))
            continue;

        String_Append(s, entry->d_name);
        String_Append(s, ";");
    }

    if (LEAK_POS > s->len) {
        puts(LEAK_WA_ANS);
        return 0;
    }

    char ch = s->str[LEAK_POS];
    closedir(dir);
    String_Delete(s);
    return ch;
}
