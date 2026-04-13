## WTF

**wtf** is an AI-powered CLI debugging assistant.

It helps you:

* explain errors and crashes
* detect issues like segmentation faults
* automatically fix broken code
* stay entirely in your terminal

No context switching. No googling cryptic errors. Just run `wtf`.

---

## Example

### Broken code

```c
// error.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* get_message() {
    char buffer[32];
    strcpy(buffer, "Hello from wtf!");
    return buffer;
}

int main() {
    char* msg = get_message();

    char* tmp = malloc(16);
    strcpy(tmp, "temporary");
    free(tmp);

    printf("%s\n", msg);
    return 0;
}
```

---

### Build and run

```bash
gcc error.c -o error
./error
```

Output:

```text
Segmentation fault (core dumped)
```

---

### Fix it with `wtf`

```bash
wtf fix error.c
```

---

### Result

`wtf` analyzes the crash and rewrites the code:

```c
// error.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* get_message() {
    char* buffer = malloc(32);
    strcpy(buffer, "Hello from wtf!");
    return buffer;
}

int main() {
    char* msg = get_message();

    char* tmp = malloc(16);
    strcpy(tmp, "temporary");
    free(tmp);

    printf("%s\n", msg);
    free(msg);
    return 0;
}
```

---

### Output

```text
Hello from wtf!
```

---

## Why wtf?

* ⚡ Instant error explanations
* 🧠 AI-powered debugging
* 🔧 Automatic code fixes
* 🖥️ Works directly in your terminal

---

## License

This project is licensed under the GPL-3.0 License.
