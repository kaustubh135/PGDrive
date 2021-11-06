<br/>
<p align="center">
  <a href="https://github.com/kaustubh135/PGDrive">
    <img src="https://github.com/kaustubh135/PGDrive/blob/main/images/logo.png" alt="Logo" width="135" height="80">
  </a>

  <h3 align="center">PGDrive</h3>

  <p align="center">
    A Simple Tool for Google Drive.
    <br/>
    <br/>
  </p>
</p>

![Contributors](https://img.shields.io/github/contributors/kaustubh135/PGDrive?color=dark-green) ![Forks](https://img.shields.io/github/forks/kaustubh135/PGDrive?style=social) ![Stargazers](https://img.shields.io/github/stars/kaustubh135/PGDrive?style=social) ![Issues](https://img.shields.io/github/issues/kaustubh135/PGDrive) ![License](https://img.shields.io/github/license/kaustubh135/PGDrive) 

## Built With

Used PyDrive2 an Google Drive API Wrapper for Python to perform all functions with Google Drive. 

## Getting Started

To get started you need to get OAuth2.0 for authentication with Google Drive API and required Python Modules.

### Prerequisites

You need to install required Python modules from requirements.trxt

* python3.9+

```sh
pip install -r requirements.txt
```

### Installation

1. Go to [APIs Console](https://console.developers.google.com/iam-admin/projects) and make your own project.

2. Search for ‘Google Drive API’, select the entry, and click ‘Enable’.

3. Select ‘Credentials’ from the left menu, click ‘Create Credentials’, select ‘OAuth client ID’.

4. Now, the product name and consent screen need to be set -> click ‘Configure consent screen’ and follow the instructions. Once finished:

5. Select ‘Application type’ to be Web application.

6. Enter an appropriate name.

7. Input http://localhost:8080/ for ‘Authorized redirect URIs’.

8. Click ‘Create’.

9. Click ‘Download JSON’ on the right side of Client ID to download client_secret_<really long ID>.json.

The downloaded file has all authentication information of your application. Rename the file to “client_secrets.json” and place it in your working directory.

## License

Distributed under the MIT License. See [LICENSE](https://github.com/kaustubh135/PGDrive/blob/main/LICENSE.md) for more information.

