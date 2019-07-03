try:
    from setuptools import setup, find_packages
    setup(
        name="amqp_server",
        version="1.0",
        package_dir={''},
        packages=find_packages(),
        scripts=['server.py'],
        install_requires=['pika>=1.0.1'],
        package_data={
            '': ['*.txt', '*.rst'],
        },
        author="Xavier AMORENA",
        author_email="xavier.amorena@labri.fr",
        description="AMQP Server",
        keywords="AMQP, Server",
        url="https://github.com/xamorena/amqp_server.git",
        project_urls={
            "Source Code": "https://github.com/xamorena/amqp_server.git",
        },
        classifiers=[
            'License :: OSI Approved :: Python Software Foundation License'
        ]
    )
except:
    import logging
    logging.error("OUPS! sorry, an error occur ...")
