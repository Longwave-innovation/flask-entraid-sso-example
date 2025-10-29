from app import create_app

app = create_app()

if __name__ == '__main__':
    app.logger.info('Starting the application')
    app.logger.info(f'Environment: {app.config}')
    app.run(debug=True, port=app.config['PORT'])