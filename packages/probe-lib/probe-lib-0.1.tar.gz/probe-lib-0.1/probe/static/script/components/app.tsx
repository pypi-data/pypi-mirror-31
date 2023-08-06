import * as React from 'react';

import { Observable } from 'rxjs/Observable'
import { Model } from '../model';

import { EventList } from './eventlist';
import { FilterInput } from './filterinput';

const StreamedEventList = streamed<{onToggleEvent: any}, {events: any[]}>(EventList);
const StreamedFilterInput = streamed<{onChange: any}, {value: string}>(FilterInput);


export const App: React.SFC<{model: Model}> = ({model}) => (
    <main>
        <header>
            <StreamedFilterInput
                stream={model.filter.map(value => ({value}))}
                onChange={model.requestEvents}
            />
        </header>
        <StreamedEventList
            stream={model.eventlist.map(events => ({events}))}
            onToggleEvent={model.toggleEvent}
        />
        <button onClick={model.loadMore}>Load more</button>
    </main>
);


function streamed<Props, T>(X: React.StatelessComponent<Props & T>) {
    return class StateToProp extends React.Component<Props & {stream: Observable<T>}, T> {

        componentWillMount() {
            this.props.stream.subscribe(value => this.setState(value))
        }

        render() {
            return <X {...this.state} {...this.props}>
                { this.props.children }
            </X>
        }
    }
}
