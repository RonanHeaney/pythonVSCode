import { ChildProcess, SpawnOptions as ChildProcessSpawnOptions } from 'child_process';
import * as Rx from 'rxjs';
import { CancellationToken, Uri } from 'vscode';

export interface IBufferDecoder {
    decode(buffers: Buffer[], encoding: string): string;
}

export type Output<T extends string | Buffer> = {
    source: 'stdout' | 'stderr';
    out: T;
};
export type ObservableExecutionResult<T extends string | Buffer> = {
    proc: ChildProcess;
    out: Rx.Observable<Output<T>>;
};

// tslint:disable-next-line:interface-name
export type SpawnOptions = ChildProcessSpawnOptions & {
    encoding?: string;
    cancellationToken?: CancellationToken;
    mergeStdOutErr?: boolean;
    throwOnStdErr?: boolean;
};

export type ExecutionResult<T extends string | Buffer> = {
    stdout: T;
    stderr?: string;
};

export interface IProcessService {
    execObservable(file: string, args: string[], options: SpawnOptions): ObservableExecutionResult<string>;
    exec(file: string, args: string[], options: SpawnOptions): Promise<ExecutionResult<string>>;
}

export interface IPythonExecutionFactory {
    create(resource?: Uri): IPythonExecutionService;
}
export interface IPythonExecutionService {
    isRunnable(): Promise<boolean>;

    getVersion(): Promise<string>;
    getExecutablePath(): Promise<string>;
    isModuleInstalled(moduleName: string): Promise<boolean>;

    execObservable(args: string[], options: SpawnOptions): ObservableExecutionResult<string>;
    execModuleObservable(module: string, args: string[], options: SpawnOptions): ObservableExecutionResult<string>;

    exec(args: string[], options: SpawnOptions): Promise<ExecutionResult<string>>;
    execModule(module: string, args: string[], options: SpawnOptions): Promise<ExecutionResult<string>>;
}

export class StdErrError extends Error {
    constructor(message: string) {
        super(message);
    }
}
