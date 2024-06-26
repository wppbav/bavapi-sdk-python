# `bavapi` Roadmap

!!! success "`bavapi` has now reached **stable** (`v1`) status"

## `v1` Roadmap - COMPLETED

This is a non-exhaustive list of potential features & changes to `bavapi` before it is ready for full release:

### Core tooling

- [x] `v0.6.0` ~~`pydantic` V2 support~~
- [x] `v0.9.0` ~~Strict `mypy` support with [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `Unpack` and `TypedDict`~~
- [x] `v0.11.0` ~~Ability to use custom `bavapi.Query` objects in endpoint methods and functions~~
- [x] `v0.11.0` ~~Improved importing experiece when using reference classes created via the `bavapi-gen-refs` command~~
- [x] `v0.12.0` ~~Ability to control pagination for performing a lot of requests.~~

### Known issues

- [x] `v0.13.0` ~~Sporadic `SSL: CERTIFICATE_VERIFY_FAILED` errors when making requests to the Fount API.~~

### Fully-supported endpoints

Eventually, the plan is to support almost all endpoints. This is the current priority list:

- [x] `v0.1.0` ~~Brands~~
- [x] `v0.1.0` ~~Brandscape Data~~
- [x] `v0.1.0` ~~Studies~~
- [x] `v0.4.0` ~~Audiences~~
- [x] `v0.10.0` ~~Categories~~
- [x] `v0.10.0` ~~Collections~~
- [x] `v0.10.0` ~~Brand Metrics~~
- [x] `v0.10.0` ~~Sectors~~
- [x] `v0.10.0` ~~Brand Metric Groups~~
- [x] `v1.0.0` ~~Cities~~
- [x] `v1.0.0` ~~Companies~~
- [x] `v1.0.0` ~~Countries~~
- [x] `v1.0.0` ~~Regions~~
- [x] `v1.0.0` ~~Years~~

### Stretch goals

- [x] `v0.8.1` ~~Smarter flattening of JSON responses, possibly through `pandas.json_normalize`.~~
