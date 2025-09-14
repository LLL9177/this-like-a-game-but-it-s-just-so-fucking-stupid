#include <stdio.h>
#include <cs50.h>
#include <string.h>

int main(void)
{
    string text = get_string("Enter your text input: ");
    int n = get_int("How much letters do you want to shift: ");

    for (int i = 0, j = strlen(text); i < j; i++)
    {
        char c = text[i];

        if (c >= 'a' && c <= 'z')
        {
            printf("%c", ((c - 'a' - n + 26) % 26) + 'a');
        }
        else if (c >= 'A' && c <= 'Z')
        {
            printf("%c", ((c - 'A' - n + 26) % 26) + 'A');
        }
        else
        {
            printf("%c", c); // non-letters unchanged
        }
    }

    printf("\n");
}
