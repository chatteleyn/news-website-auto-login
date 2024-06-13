# News websites auto-login

A proxy that returns then content of a website authenticated/logged-in with your own credentials.

This project was originally developed so that you could read articles with a paywall or that require a connection on a Kobo e-reader using Pocket. Feel free to use this project for anything else.

## Configuration

You can configure the websites you want with your own credentials and settings by modifying the `website_config.json` file. Two examples for the [mediapart.fr](https://www.mediapart.fr/) and [monde-diplomatique.fr](https://www.monde-diplomatique.fr/) websites are already in the file.

- `login_url`: This is the url present in the action attribute in the HTML login form 
- `login`: This is the parameters that will be injected in the POST request to log in
- `not_logged_in`: This is the XPATH of the HTML element is the page that shows you are not logged-in
- `strip`: List of XPATH for HTML elements to remove from the result
- `move`: List of HTML elements to move from the result. The format is `[origin XPATH, target XPATH, position]` where position is the position from the target and can can be `inside-up` , `inside-bottom`, `outside-up`  or `outside-bottom`

- You can use environment variables by surrounding it with `$…$`
- You can use XPATH by surrounding it with `xpath(…)`




## Usage

```bash
pip install -r requirements.txt
python proxy.py
```
Use the proxy by accessing `<address>?url=<url-encoded>` on your browser where `<address>`is the address of the server and `<url-encoded>` is the encoded url of the webpage you want to retrieve.

## Deployment

You'll find `vercel.json`, a config file to deploy the proxy on Vercel. You can choose to deploy this project on another service or on your own.

## Contributing

Feel free make a pull request or to open a ticket for any feature request, issue or question.

## License

[MIT](https://choosealicense.com/licenses/mit/)