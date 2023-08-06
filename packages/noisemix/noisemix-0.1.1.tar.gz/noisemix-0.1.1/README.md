NoiseMix is a library for [data generation](http://cs231n.stanford.edu/reports/2017/pdfs/300.pdf) for text datasets.

Data generation or augmentation with perturbations or distortions is a technique so successful in image tasks that support for it is included in major frameworks like [PyTorch](http://pytorch.org/tutorials/beginner/data_loading_tutorial.html#transforms), [Tensorflow](https://www.tensorflow.org/tutorials/deep_cnn#convolutional-neural-networks) and [Keras](https://keras.io/preprocessing/image/).

However, data generation is not yet for common for natural language tasks.  (Why?  Well, arguably it is more difficult to generate realistic noise for data with many discontinuities.)  For more on how NoiseMix can increase performance on various tasks, see [Benchmarks](#benchmarks).

NoiseMix adds new rows to datasets by applying changes to copies of existing rows.  For example, consider:
> This was a great book, but their shipping was too slow.  

After augmentation, we have the original row plus a few new versions:  
> This was a great book, but their shipping was too slow.  
> This was a great book but there shipping was too slow.  
> this was a great book, but their shipping was to slow.  

Thus the generated dataset is at least twice as large as the original.

#### Installing

For required packages, run:
```
pip install -r requirements.txt
```

#### Running
To generate the noisy data, call the program with the path to your fastText data file, for example:

```
  python noisemix.py train.ft.txt
```
This will generate a data file with the added suffix `.nmx`.

##### Parameters

NoiseMix offers word-level and sentence-level perturbations.

The word-level perturbations are:
add_letter, repeat_letter, remove_letter, lowercase, remove_punct, word_swap, char_swap, flip_letters and typo_qwerty (creating a reaslitic typo based on keyboard layout)
The sentence-level perturbations are:
remove_space and flip_words

Each of the perturbation can be enabled/disabled, repeated multiple times per line and frequency


#### Supported data formats

To be usable for labelled datasets, NoiseMix keeps intact non-language formatting like labels and delimiters.

[fastText](https://fasttext.cc/) (`__label__` prefix) is the only supported format for now.

Suggest a new data format by [opening an issue](../../issues/new?title=Support+for+new+data+format)

English is the only supported language at the moment and the supported keyboard layout is QWERTY

#### Benchmarks

To test the effectiveness of NoiseMix, we compare it control data on several benchmarks.  Several benchmarks and toy datasets are included.

See results and more in [benchmarks/](benchmarks/)

#### Developing

To make contributions, just `git clone` this repo or a fork of it, and submit a pull request with your changes.

##### Adding a new language

Beyond parameters that can be adjusted for the specifics of each language, NoiseMix includes hand-built lists of common noise for each language.

For example, in English corpora erroneous swaps of `there` and `their` are common, in Italian it is common for users without an Italian keyboard to type word-final `a' ` instead of `á `.

Add lists for new languages to [noise/data.py](noise/data.py).