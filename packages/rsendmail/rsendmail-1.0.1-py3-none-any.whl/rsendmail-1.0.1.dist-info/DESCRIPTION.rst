A wrapper for the sendmail command which allows calling sendmailwithout allowing side effects traditionnally allowed by sendmailbinaries (like flushing the queue or reloading the alias files). Thisis designed to be ran from an SSH command and be safely assignedas a authorized_keys `command=` parameter.


