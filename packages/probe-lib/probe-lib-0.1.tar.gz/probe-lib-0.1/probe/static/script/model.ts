import { Observable } from 'rxjs/Observable'
import { Subject } from 'rxjs/Subject'

import * as api from './api';
import { Document } from './api';

import 'rxjs/add/observable/combineLatest';
import 'rxjs/add/observable/concat';
import 'rxjs/add/observable/of';
import 'rxjs/add/observable/merge';

import 'rxjs/add/operator/scan';
import 'rxjs/add/operator/concat';
import 'rxjs/add/operator/mergeScan';


export interface ProbeEvent extends api.ProbeEvent {
    expanded: boolean,
}


function eventListStream(filter: Observable<string>,
                            more: Observable<null>): Observable<api.ProbeEvent[]> {

    return Observable
        .merge(
            filter.map(text =>
                (doc: Document) => Document.fetch(text)),
            more.map(_ =>
                (doc: Document) => doc.more())
        )
        .mergeScan((state, func) => func(state), Document.empty())
        .map(doc => doc.events)
}


export class Model {

    private readonly actionEventToggle = new Subject<string>();
    private readonly actionFilterChange = new Subject<string>();
    private readonly actionLoadmore = new Subject<null>();

    private readonly expanded: Observable<string[]>;
    public readonly filter: Observable<string>;
    public readonly eventlist: Observable<ProbeEvent[]>;

    constructor() {
        this.toggleEvent = this.toggleEvent.bind(this);
        this.requestEvents = this.requestEvents.bind(this);
        this.loadMore = this.loadMore.bind(this);

        this.filter = this.constructFilter();
        this.expanded = this.constructExpanded();
        this.eventlist = this.constructEventlist();
    }

    private constructFilter() {
        return this.actionFilterChange.scan((last, value) => value, '');
    }

    private constructExpanded() {
        return Observable
            .of([] as string[])
            .concat(
                this.actionEventToggle
                    .scan((ids, id) => (ids.indexOf(id) === -1)
                                        ? ids.concat([id])
                                        : ids.filter(item => item !== id), []));
    }

    private constructEventlist() {
        return Observable.combineLatest(
            eventListStream(this.actionFilterChange, this.actionLoadmore),
            this.expanded,
            (events, expandedIDs) => events.map(evt =>
                    ({...evt, expanded: expandedIDs.indexOf(evt.id) !== -1}))
        );
    }

    toggleEvent(id: string) {
        this.actionEventToggle.next(id);
    }

    requestEvents(filter: string) {
        this.actionFilterChange.next(filter);
    }

    loadMore() {
        this.actionLoadmore.next(null);
    }

}
