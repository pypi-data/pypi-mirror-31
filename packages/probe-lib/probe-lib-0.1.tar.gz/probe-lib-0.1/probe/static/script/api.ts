import { Observable } from 'rxjs/Observable'

import 'rxjs/add/observable/dom/ajax';
import 'rxjs/add/operator/map';


export interface ProbeEvent {
    id: string,
    type: string,
    description: string[],
    datetime: Date,
}


interface Response {
    events: ProbeEvent[]
};

export function fetchEvents(filter: string, until?: string): Observable<ProbeEvent[]> {
    return Observable
        .ajax({
            method: "GET",
            url: '/api/events/'
                    + `?filter=${encodeURIComponent(filter)}`
                    + `&until=${until || ''}`
        })
        .map(r => r.response as Response)
        .map(r => r.events.map(evt => ({
            ...evt,
            datetime: new Date(evt.datetime)
        })));
}


export class Document {

    public readonly events: ProbeEvent[]
    private readonly filter: string;

    public static empty(): Document {
        return new Document('', []);
    }

    public static fetch(filter: string): Observable<Document> {
        return fetchEvents(filter).map(events => new Document(filter, events))
    }

    constructor(filter: string, events: ProbeEvent[]) {
        this.filter = filter;
        this.events = events;
    }

    public more(): Observable<Document> {
        let last = this.events[this.events.length - 1];
        return fetchEvents(this.filter, last && last.id)
                    .map(events => new Document(this.filter, this.events.concat(events)))
    }
}
