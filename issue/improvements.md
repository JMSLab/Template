1. In `source/lib/JMSLab/builders/build_stata.py` I'd like to be able either have a) the log file directly written into the final location so we don't need the finalize_log_file function, or b) I'd like to have the function be renamed to move_log_to_log_folder
    - Also please go back to calling it do_call
    - Also is there no way to super the StataBuilder?
2. In `source/lib/JMSLab/tests/_test_helpers.py` and `source/lib/JMSLab/builders/jmslab_builder.py` with respect to the function defining the log file location - I don't understand why we can't define `get_log_file_path` purely within the builder class and then import that function in source/lib/JMSLab/tests/_test_helpers.py, as opposed to importing the external function. Also, if we can't do that or it doesn't align with good SWE principles we can keep the external function in a builders helpers script. 
3. In `source/lib/JMSLab/builders/jmslab_builder.py` I don't get why i need all these extra exceptions. 
3. Should you clean up log files in `source/lib/JMSLab/tests/log/bad_dir/` post testing?? Also `source/lib/JMSLab/tests/log/test.log` 
4. Why are we asserting false here? 
```
helpers.check_log(self, helpers.expected_log_path('test_script.do'), 'failed')
self.assertFalse((TESTDIR / 'test_script.log').exists())
```

5. `test_end_log_appends_builder_logs_from_log_directory` what is this doing here? 
6. Explain the new tests in source/lib/JMSLab/tests/test_log.py?