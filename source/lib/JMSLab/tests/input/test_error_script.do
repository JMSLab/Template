* Script errors after producing all targets
file open f using "test_output.txt", write replace
file write f "Test output"
file close f
assert 1 == 2
