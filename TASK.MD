evaluate python and mojo implementations of the m-n-k game.

run tests with:
.venv/bin/python -m pytest test.py
magic run mojo src/test.mojo

play games with:
.venv/bin/python src/play.py
magic run mojo src/play.mojo

to benchmark single evaluation:
magic run mojo build src/benchmark_mojo_single.mojo
hyperfine --warmup 3 .venv/bin/python benchmark_python_single.py benchmark_mojo_single

to benchmark batch evaluation:
magic run mojo build src/benchmark_mojo_multi.mojo
hyperfine --warmup 3 .venv/bin/python benchmark_python_multi.py benchmark_mojo_multi

to play:
magic run mojo build src/play.mojo
./play 3 3 1 (board size 3,3 with depth 1) should result in: Player 1 wins!
./play 3 3 2 (board size 3,3 with depth 2) should result in: Game is a draw!

current task:
add more evaluate tests, and make sure they cover all edge cases. then update the actual eval code to implement any learnings.

notes:
1. favor fully functional programming and code simplicity
2. before proposing a change, ask yourself "how does the proposed change solve the problem?"
3. focus on small diffs
4. mojo uses `var` not `let`
5. use `magic run mojo` instead of `mojo`
6. DynamicVector doesn't exist
7. the Mojo stdlib is cloned in `/code/mojo/stdlib`
8. ask permission before making major functional changes