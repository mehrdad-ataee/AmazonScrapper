import time
import ASCore as Core
import ASConfig as Config

def get_user_request():
    request = input('Press S for scrapping,\n'
          'Press C for converting the existing data to CSV \n'
          'Press F to fix all faulty collected data \n'
          'Then -> \n'
          'Press Enter...')
    if request.lower() == 's':
        return 1
    elif request.lower() == 'c':
        return 2
    elif request.lower() == 'f':
        return 3
    else:
        print('Please enter a valid request...')
        time.sleep(0.5)
        get_user_request()


if __name__ == '__main__':
    answer = get_user_request()
    print('Answer is '.format(answer))
    core = Core.RipperCore()

    if answer == 1:
        input('Make sure you have placed \n'
              'all product links you want to scrap \n'
              'in a text file named[{0}] and press Enter...'.format(Config.products_links_source_name))
        core.initiate()
    elif answer == 2:
        input('All records in your database will be converted to file Named[{0}.csv] \n'
              'Press Enter to begin...'.format(Config.output_database_name))
        core.export_database_to_csv()
    else:
        input('All faulty scrapped data in your database will be scrapped again, \n'
              'this will not fix them if they are caused by permanent server sided issues \n'
              'Press Enter to begin...')
        core.fix_faulty_reviews()


