import * as React from 'react';


interface ButtonProps {
    state: boolean,
    onClick: () => any,
}


export const Button: React.SFC<ButtonProps> = ({onClick, state}) => (
    <button onClick={onClick}>
        <span className={state ? 'fa fa-compress' : 'fa fa-expand'} />
    </button>
);
