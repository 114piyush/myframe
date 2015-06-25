# Hello world test to display information passed at command line
import framework.config

def Run(args):
    log = args['logObj'].log
    log.info('I am log of helloworld test')
    log.info('Printing user input')
    for key, value in args.items():
        log.info("%s : %s" % (str(key),str(value)) )
	if isinstance(value, framework.config.Config):
	    for k,v in vars(value).items():
                log.info("    %s : %s" % (str(k),str(v)) )
