# News Websites Auto-Login

A proxy server that returns the content of a website authenticated/logged-in with your own credentials.

This project was originally developed to enable reading articles with a paywall or that require login credentials on a Kobo e-reader using Pocket. Feel free to adapt this project for other uses.

## Table of Contents

- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Configuration

To configure the websites with your own credentials and settings, modify the `website_config.json` file. Example configurations for [mediapart.fr](https://www.mediapart.fr/) and [monde-diplomatique.fr](https://www.monde-diplomatique.fr/) are provided.

### Configuration Parameters

- `login_url`: The URL present in the action attribute of the HTML login form.
- `login`: The parameters to be injected in the POST request to log in.
- `not_logged_in`: The XPath of the HTML element indicating the user is not logged in.
- `strip`: A list of XPath expressions for HTML elements to remove from the result.
- `move`: A list of HTML elements to move within the result. Format: `[origin XPath, target XPath, position]` where position can be `inside-up`, `inside-bottom`, `outside-up`, or `outside-bottom`.

### Additional Configuration Options

- Use environment variables by surrounding them with `$…$`.
- Use XPath by surrounding it with `xpath(…)`.

## Usage

Install the required dependencies and run the proxy server:

```bash
pip install -r requirements.txt
python proxy.py
```

Access the proxy by navigating to `<address>?url=<url-encoded>` in your browser, where `<address>` is the server address and `<url-encoded>` is the encoded URL of the webpage you want to retrieve.

## Deployment

The project includes a `vercel.json` configuration file for deployment on Vercel. You may also choose to deploy this project on another service or on your own server.

## Contributing

We welcome contributions! Feel free to make a pull request or open an issue for feature requests, bug reports, or questions.

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).