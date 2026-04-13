#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main() {
    printf("僵尸制造机已启动...\n");

    // fork() 会创建一个新的子进程
    pid_t pid = fork();

    if (pid < 0) {
        // fork 失败（比如 PID 资源耗尽）
        perror("fork 失败");
        return 1;
    }
    else if (pid == 0) {
        // ==========================================
        // 这里是【子进程】执行的代码
        // ==========================================
        printf("👶 [子进程] 我的 PID 是: %d。我马上要退出了，准备变身僵尸！🧟\n", getpid());

        // 子进程立刻退出。
        // 此时由于父进程还没来得及为其“收尸”（调用 wait），它将变成僵尸进程 (Z 状态)
        exit(0);
    }
    else {
        // ==========================================
        // 这里是【父进程】执行的代码
        // ==========================================
        printf("👨 [父进程] 我的 PID 是: %d。我刚刚创建了子进程 (PID: %d)。\n", getpid(), pid);
        printf("👨 [父进程] 我现在要睡上 60 秒，绝对不去管子进程的死活 (不调用 wait)。\n");
        printf("👉 请立刻打开另一个终端，运行: ps -ef | grep defunct 或者 top\n");
        printf("--------------------------------------------------\n");

        // 父进程休眠，故意不调用 wait() 或 waitpid() 去回收子进程状态
        sleep(60);

        printf("👨 [父进程] 60秒到了，我睡醒了，准备退出。\n");
        printf("✨ [父进程] 我死后，我的僵尸儿子会被 systemd/init (PID 1) 收养并超度（清理）。\n");
    }

    return 0;
}