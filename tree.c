// mytree.c
// 简单的 Linux 上的 tree 实现（C 语言）

#define _XOPEN_SOURCE 700
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <errno.h>
#include <unistd.h>
#include <limits.h>

// 是否显示隐藏文件（以 '.' 开头），true 显示，false 不显示
#define SHOW_HIDDEN 0

// 比较函数，用于 qsort（按名字排序，目录和文件混合）
static int name_cmp(const void *a, const void *b) {
    const char * const *sa = a;
    const char * const *sb = b;
    return strcmp(*sa, *sb);
}

// 列出目录并返回项列表（caller 需 free each entry 与数组）
static char **read_dir_entries(const char *path, int *cnt_out) {
    DIR *d = opendir(path);
    if (!d) return NULL;

    struct dirent *ent;
    size_t cap = 64;
    size_t n = 0;
    char **arr = malloc(cap * sizeof(char*));
    if (!arr) { closedir(d); return NULL; }

    while ((ent = readdir(d)) != NULL) {
        const char *name = ent->d_name;
        if (!SHOW_HIDDEN && name[0] == '.') continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;

        if (n >= cap) {
            cap *= 2;
            char **tmp = realloc(arr, cap * sizeof(char*));
            if (!tmp) { // 内存不足，释放已分配的字符串
                for (size_t i = 0; i < n; ++i) free(arr[i]);
                free(arr);
                closedir(d);
                return NULL;
            }
            arr = tmp;
        }
        arr[n++] = strdup(name);
    }
    closedir(d);

    if (n > 0) qsort(arr, n, sizeof(char*), name_cmp);
    *cnt_out = (int)n;
    return arr;
}

// 递归打印目录树
// prefix: 前缀字符串（包括竖线/空格）
// is_last: 指示当前目录项是否是所在目录的最后一项（用于选择 └── 或 ├──）
static void print_tree_recursive(const char *path, const char *name, char *prefix, int is_last, int depth_limit) {
    // 打印当前项的行（根目录特殊处理）
    if (name != NULL) {
        printf("%s%s%s\n", prefix, is_last ? "└── " : "├── ", name);
    } else {
        // 根路径：打印 path 本身
        printf("%s\n", path);
    }

    // 如果 name != NULL，构造 fullpath，否则 path 已经是根路径
    char fullpath[PATH_MAX];
    if (name) {
        // path 为父目录路径，拼接 name
        if (snprintf(fullpath, sizeof(fullpath), "%s/%s", path, name) >= (int)sizeof(fullpath)) {
            // 路径太长，跳过递归
            return;
        }
    } else {
        strncpy(fullpath, path, sizeof(fullpath));
        fullpath[sizeof(fullpath)-1] = '\0';
    }

    // 检查是否为目录（但不要跟随符号链接）
    struct stat st;
    if (lstat(fullpath, &st) != 0) {
        // 无法 stat，直接返回
        return;
    }

    if (!S_ISDIR(st.st_mode)) {
        // 不是目录，结束
        return;
    }

    if (depth_limit == 0) return;

    // 读取目录项
    int n = 0;
    char **entries = read_dir_entries(fullpath, &n);
    if (!entries) return;

    // 为每个子项递归打印，构造下一级 prefix
    for (int i = 0; i < n; ++i) {
        int child_is_last = (i == n - 1);

        // 构造 new_prefix：当前行如果不是最后则需要保留竖线 "│   "，否则保留空格 "    "
        size_t pref_len = strlen(prefix);
        char new_prefix[1024];
        if (name == NULL) {
            // 根的 prefix 通常为空
            if (pref_len + 5 >= sizeof(new_prefix)) continue;
            strcpy(new_prefix, prefix);
        } else {
            if (pref_len + 5 >= sizeof(new_prefix)) continue;
            strcpy(new_prefix, prefix);
        }

        // 如果当前层（即打印 name 的那一层）是最后，则不需要在新前缀里保留竖线
        // 我们需要检查上一次调用传入的 is_last 来决定当前层是否保留竖线
        // 但是为了简单性，我们在上级已经把 prefix 构造为包含正确的 "│   " 或 "    "
        // 这里只追加一个级别的占位
        strcat(new_prefix, (is_last ? "    " : "│   "));

        // 递归
        print_tree_recursive(fullpath, entries[i], new_prefix, child_is_last, depth_limit > 0 ? depth_limit - 1 : -1);
        free(entries[i]);
    }
    free(entries);
}

int main(int argc, char **argv) {
    const char *start = "/";
    int depth_limit = -1; // -1 表示无限深度

    // 简单解析命令行：mytree [path] 或 mytree -L depth [path]
    int argi = 1;
    while (argi < argc) {
        if (strcmp(argv[argi], "-L") == 0 && argi + 1 < argc) {
            depth_limit = atoi(argv[argi + 1]);
            if (depth_limit < 0) depth_limit = -1;
            argi += 2;
        } else {
            start = argv[argi++];
        }
    }

    // 取开始路径的真实路径（如果需要）
    char real_start[PATH_MAX];
    if (realpath(start, real_start) == NULL) {
        // realpath 失败就用原始 start（可能是相对路径）
        strncpy(real_start, start, sizeof(real_start));
        real_start[sizeof(real_start)-1] = '\0';
    }

    // 打印根节点（使用 real_start 的最后一段或路径本身）
    // 为了与 tree 类似，打印起始目录名，而不是完整路径
    const char *start_name = real_start;
    // 找到最后一个 '/'
    const char *p = strrchr(real_start, '/');
    if (p && *(p+1) != '\0') start_name = p + 1;

    // 如果 start_name 为空（例如根目录），则打印 real_start
    if (start_name[0] == '\0') {
        printf("%s\n", real_start);
        start_name = NULL; // 这样递归会把 path 当作根
    }

    char prefix[1024] = ""; // 初始前缀为空
    print_tree_recursive(real_start, start_name, prefix, 1, depth_limit);

    return 0;
}
