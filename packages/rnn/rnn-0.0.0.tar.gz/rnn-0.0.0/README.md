Recurrent Neural Networks using TensorFlow.


## Installation

```sh
pip install rnn
```

It is recommended to use a [virtual environment].


## Getting Started

```py
from rnn import LSTM

model = LSTM(units=128, projections=300)
outputs = model(inputs)
```

### Sequence Generation

```py
from rnn import Generator

sequence = Generator(model)
sample = sequence(seed, length)
```


## License

[MIT][license]


[license]: /LICENSE
[virtual environment]: https://docs.python.org/3/library/venv.html
