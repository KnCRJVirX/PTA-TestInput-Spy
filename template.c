// #define LEAK_POS __LEAK_Pos
// #define NUMBER_ONLY __NUMBER_Only
#define LEAK_POS 0
#define NUMBER_ONLY 0
#define LEAK_WA_ANS "__PTA_TestInput_Spy__"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

char NumberOnlyProcess(char ch) {
    switch (ch)
    {
        case ' ':   return 10;
        case '\n':  return 11;
        case '\0':  return 12;
        case '-':   return 13;
        default:    return ch - '0';
    }
}

int main(int argc, char const *argv[])
{
    size_t memSize = 32 * 1024 * 1024;
    String* input = String_New();
    char buf[256] = {0};
    while (fgets(buf, sizeof(buf), stdin)) {
        String_Append(input, buf);
    }

    if (LEAK_POS > input->len) {
        puts(LEAK_WA_ANS);
        return 0;
    }

    char ch0 = input->str[LEAK_POS];
    if (NUMBER_ONLY) {
        char ch1 = input->str[LEAK_POS + 1];
        ch0 = NumberOnlyProcess(ch0);
        ch1 = NumberOnlyProcess(ch1);
        return ((unsigned char)ch0 << 4) | (unsigned char)ch1;
    } else {
        return ch0;
    }
    
    return 0;
}
