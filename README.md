LogMonitoring
=============

a simple logMonitoring tool with REST API.
Please download following files

    1. logWriter.py : This script randomly writes dummy log massages to one of 4 user log files, /var/log/local<0...3>
    2. logReaderStats.py: this is a command line script,it should be run by specifying filename and number of hours, any log message older than hours specified are ignored while building statistics of log messages. usage "logReaderStats.py -f <filename> -t <hours>"
    3. celeryLogReader.py is modified version of logReaderStats.py, it performs same task of statistics generation, however it is performed inside a background task, which can be controlled by celery utility. Please see following link on more information on celery,http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html. Celery in turn uses message broker, I have used rabbitMq for my application, please see following link on installation of rabbitMQ, http://www.rabbitmq.com/install-debian.html
    4. The last file is flaskLogStats.py: this script implements REST API functions HTTP "GET" and "POST" using flask REST framework, instruction on installing flask can be found at , http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
    flask is run in its own virtual envrionment with python installed in /flask/bin directory.

Both celeryLogReader.py and flaskLogStats.py are run in virtual environment.

Steps to start REST interface

    1. Start celeryLogReader.py by running following command 
        $./flask/bin/celery -A celeryLogReader worker --loglevel=info
    2. Run flaskLogStats.py
         $./flaskLogStats.py
         * Running on http://127.0.0.1:5000/
         * Restarting with reloader
    3. Open a new terminal window and send a HTTP POST request to the local host, by running command, specifying both filename and hours.
    4.  curl -i -H "Content-Type: application/json" -X POST-d '{"filename":"local0.log", "hours": 7}' http://localhost:5000/logs/api/v1.0/stats

   This would send back the results, in following JSON format        
   {
     [ 
      {
        "ERRTYPE": "INFO", 
        "STATS":[            
        {
          "PID": "7181", 
          "logtime": "2013-09-30 11:04:37"
        }, 
        {
          "PID": "7181", 
          "logtime": "2013-09-30 11:07:22"
        }, 
        {
          "PID": "7181", 
          "logtime": "2013-09-30 11:07:37"
        }
      ]
    }, 
    {
      "ERRTYPE": "EMER", 
      "STATS": []
    }
  ]
}


        

, when starting flaskLogStats.py, celeryLogReader.py needs to be in the same folder../flask/bin/celery -A celeryLogReader worker --loglevel=info
