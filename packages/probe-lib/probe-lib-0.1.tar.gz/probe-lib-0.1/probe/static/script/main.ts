import * as React from 'react';
import * as ReactDOM from 'react-dom';

import { Model } from './model';
import { App } from './components/app';

const model = new Model();

ReactDOM.render(
    React.createElement(App, {model}),
    document.querySelector('#application')
);

model.requestEvents('');
