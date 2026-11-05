// The GPU memory stop (gpu_mem_stop): past DM_GPU_MEM_STOP (default Metal's recommended working set) the host exits with status 3 before a residency commit, or at the 100 ms
// check, instead of letting the kernel fail to wire memory (a hard freeze of the Mac, Ocarina of Time). Each case runs in a child process of this test (the stop exits the process)
#include <spawn.h>
#include <sys/wait.h>
#define nvn_game_fps nvn_game_fps_mtl_default
#include "../nvn/nvn_mtl.m"
#undef nvn_game_fps
uint64_t g_t0_ns;
void *front_metal_layer(void) { return NULL; }
module_t *module_of(const void *p) { (void)p; return NULL; }
module_t *g_mod; int g_nmod;
void svc_thread_dump(void) {}
uint64_t now_ns(void) { return bp_now(); }
extern char **environ;
static int checks, failed;
#define CHECK(c, label) do { checks++; if (!(c)) { failed++; fprintf(stderr, "FAIL: %s\n", label); } } while (0)

static int child(const char *what) { @autoreleasepool {
    mtl_init();
    if (!strcmp(what, "default")) return g_gpu_stop == g_dev.recommendedMaxWorkingSetSize ? 0 : 1;
    id<MTLBuffer> b = [g_dev newBufferWithLength:8u << 20 options:MTLResourceStorageModeShared];
    memset(b.contents, 1, b.length); res_add(b);
    if (!strcmp(what, "commit")) { res_commit(); return 0; }   // the stop exits before the commit
    if (!strcmp(what, "timer")) { usleep(1000000); return 0; }   // no commit: the 100 ms check exits
    if (!strcmp(what, "off")) { res_commit(); usleep(300000); return 0; }
    return 1;
} }
static int run(const char *self, const char *what, const char *stop) {
    if (stop) setenv("DM_GPU_MEM_STOP", stop, 1); else unsetenv("DM_GPU_MEM_STOP");
    pid_t pid; char *argv[] = {(char *)self, (char *)what, NULL};
    if (posix_spawn(&pid, self, NULL, NULL, argv, environ)) return -1;
    int st = 0; if (waitpid(pid, &st, 0) != pid) return -1;
    return WIFEXITED(st) ? WEXITSTATUS(st) : 128 + WTERMSIG(st);
}
int main(int argc, char **argv) {
    if (argc > 1) return child(argv[1]);
    CHECK(run(argv[0], "default", NULL) == 0, "the stop defaults to Metal's recommended working set");
    CHECK(run(argv[0], "commit", "1") == 3, "a residency commit past the stop exits with status 3");
    CHECK(run(argv[0], "timer", "1") == 3, "the 100 ms check exits with status 3 past the stop");
    CHECK(run(argv[0], "off", "0") == 0, "DM_GPU_MEM_STOP=0 turns the stop off");
    printf("t_gpu_mem_stop: %d checks, %d failed\n", checks, failed);
    return failed != 0;
}
