package main

import "fmt"

func main() {
    const w = 6
    var (
        i, n, d int
        c int
	)
    fmt.Scan(&n)
    c = 0
    i = 2
    for i <= n {
        d = 2
        for i % d != 0 {
            d++
        }
        if d == i { /* i - простое */
            c++; fmt.Println(i)
        }
        i++
	}
}
