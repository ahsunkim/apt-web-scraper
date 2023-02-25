# apt-web-scraper

WIP Project! 

This Python project scrapes apartment rent listings from Apartments.com and stores the data in a PostgreSQL database. It also provides a GraphQL API that allows you to query the apartment data using the GraphiQL interface.

## Installation
To install the necessary dependencies, first set up your virtual env:
```
virtualenv myenv
source myenv/bin/activate
```

Once in your virtual env, install your dependencies:
```
pip install beautifulsoup4 psycopg2 sqlalchemy flask flask-graphql graphene graphene_sqlalchemy apache-airflow
```

TO-DO: Move to requirements.txt

## Database Setup
Make sure Postgres is running locally

Create new Postgres DB locally - type in the following into your cli
```
psql -U {username}
createdb apartment
```

## Configuration
To configure the PostgreSQL database connection URL, edit the `DATABASE_URL` variable in the `apartment_scraper.py` and `app.py` files to match your PostgreSQL database credentials.

## Usage
To run the scraper to populate the db, run the following command:
```
python apartment_scraper.py
```

To start the GraphQL server, run the following command:
```
python app.py
```

This will run the scraper and store the data in the PostgreSQL database. It will also start the GraphQL server and serve the API on the `http://localhost:5000/graphql` endpoint.

To query the apartment data, you can use the GraphiQL interface by visiting the `http://localhost:5000/graphql` endpoint in your web browser. Here's an example query that retrieves all the apartments:
```
{
  allApartments{
    edges{
      node{
        url
        price
      }
    }
  }
}
```

This will return a JSON response with the url and price of all the apartments in the database.
