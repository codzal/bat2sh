$queue = [System.Collections.Generic.Queue[string]]::new()
"task1","task2","task3" | ForEach-Object { $queue.Enqueue($_) }
while ($queue.Count -gt 0) { "serving $( $queue.Dequeue() )" }
"queue empty"
