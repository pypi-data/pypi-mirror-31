# revise-x
Use this python package to export models trained with [keras](https://github.com/keras-team/keras "keras") into a format that can be consumed by [revise](https://github.com/noheltcj/revise "revise") for use in other platforms.

## Documentation
Currently revise does not support all neural architectures, optimizers, or activation functions.

For a list of supported functions, see the [revise documentation](https://github.com/noheltcj/revise "revise documentation").

### Keras
```
from revise import keras as exporter
exporter.export()
```

## Contributing
We still haven't setup ground rules for contribution. For now, open up a pull request if you would like to contribute, and we will go from there.
