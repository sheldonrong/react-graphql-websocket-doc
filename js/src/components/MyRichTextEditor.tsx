import * as React from 'react';
import { Button, Icon } from 'semantic-ui-react';
import { Editor, EditorState, RichUtils } from 'draft-js';

type MyRichTextEditorState = {
    editorState: EditorState
}

export class MyRichTextEditor extends React.Component<{}, MyRichTextEditorState> {

    constructor(props: any) {
        super(props);
        this.state = {
            editorState: EditorState.createEmpty()
        };
    }

    public onChange = (editorState: EditorState) => {
        return this.setState({editorState})
    }

    public toggleInlineStyle = (style: string) => {
        this.onChange(RichUtils.toggleInlineStyle(this.state.editorState, style));
    }

    public render() {
        return (
            <div>
                <Button.Group>
                    <Button icon onClick={(e, data) => this.toggleInlineStyle('BOLD')}>
                        <Icon name='bold' />
                    </Button>
                    <Button icon onClick={(e, data) => this.toggleInlineStyle('ITALIC')}>
                       <Icon name='italic' />
                    </Button>
                    <Button icon onClick={(e, data) => this.toggleInlineStyle('UNDERLINE')}>
                        <Icon name='underline' />
                    </Button>
                </Button.Group>
                <Editor editorState={this.state.editorState} onChange={this.onChange}/>
            </div>
        )
    }
}