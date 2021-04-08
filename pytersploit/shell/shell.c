#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <termios.h>
#include <pthread.h>

#define CTRL_KEY(k) ((k)&0x1f)

struct termios orig_termios;
FILE *input, *output;
pthread_t stdin_thread, stdout_thread;

void die(const char *s)
{
    if (pthread_self() == stdin_thread || pthread_self() == stdout_thread) {
        printf("%s", s);
        pthread_cancel(stdin_thread);
        pthread_cancel(stdout_thread);
    } else {
        fclose(input);
        fclose(output);
        sleep(1);
        exit(0);
    }
}

void disable_raw_mode()
{
    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios) == -1)
        die("tcsetattr");
}

void enabled_raw_mode()
{
    if (tcgetattr(STDIN_FILENO, &orig_termios) == -1)
        die("tcgetattr");
    atexit(disable_raw_mode);

    struct termios raw = orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    //   raw.c_cc[VMIN] = 0;
    //   raw.c_cc[VTIME] = 1;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1)
        die("tcsetattr");
}

void stdin_to_output(void *_)
{
    fprintf(output, "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n");
    while (1)
    {
        char c;
        if (read(0, &c, 1) < 1)
        {
            die("Stdin stream EOF, quiting...\n");
            break;
        }
        else if (c == CTRL('q'))
        {
            die("Qutting...\n");
            break;
        }
        fprintf(output, "%c", c);
    }
}

void input_to_stdout(void *_)
{
    while (1)
    {
        int c = fgetc(input);
        if (c == EOF)
        {
            die("Stdout stream EOF, quiting...\n");
            break;
        }
        printf("%c", c);
    }
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Must be called with two filename arguments\n");
        exit(-1);
    }

    input = fopen(argv[1], "r");
    setbuf(input, NULL);
    output = fopen(argv[2], "w");
    setbuf(output, NULL);

    enabled_raw_mode();

    pthread_create(&stdin_thread, NULL, (void *)&stdin_to_output, NULL);    
    pthread_create(&stdout_thread, NULL, (void *)&input_to_stdout, NULL);

    pthread_join(stdin_thread, NULL);
    pthread_join(stdout_thread, NULL);

    die("");
}
