import { EnvironmentVariables } from '../variables/types';
import { ExecutionResult, IProcessService, IPythonExecutionService, ObservableExecutionResult, SpawnOptions } from './types';

export class PythonExecutionService implements IPythonExecutionService {
    constructor(private pythonPath: string, private envVars: EnvironmentVariables | undefined, private procService: IProcessService) { }
    public async getVersion(): Promise<string> {
        return this.procService.exec(this.pythonPath, ['--version'], { env: this.envVars, mergeStdOutErr: true })
            .then(output => output.stdout.trim());
    }
    public async getExecutablePath(): Promise<string> {
        return this.procService.exec(this.pythonPath, ['-c', 'import sys;print(sys.executable)'], { env: this.envVars, throwOnStdErr: true })
            .then(output => output.stdout.trim());
    }
    public async isModuleInstalled(moduleName: string): Promise<boolean> {
        return this.procService.exec(this.pythonPath, ['-c', `import ${moduleName}`], { env: this.envVars, throwOnStdErr: true })
            .then(() => true);
    }

    public execObservable(args: string[], options: SpawnOptions): ObservableExecutionResult<string> {
        const opts: SpawnOptions = { ...options };
        if (this.envVars) {
            opts.env = this.envVars;
        }
        return this.procService.execObservable(this.pythonPath, args, opts);
    }
    public execModuleObservable(moduleName: string, args: string[], options: SpawnOptions): ObservableExecutionResult<string> {
        const opts: SpawnOptions = { ...options };
        if (this.envVars) {
            opts.env = this.envVars;
        }
        return this.procService.execObservable(this.pythonPath, ['-m', moduleName, ...args], opts);
    }
    public async exec(args: string[], options: SpawnOptions): Promise<ExecutionResult<string>> {
        const opts: SpawnOptions = { ...options };
        if (this.envVars) {
            opts.env = this.envVars;
        }
        return this.procService.exec(this.pythonPath, args, opts);
    }
    public async execModule(moduleName: string, args: string[], options: SpawnOptions): Promise<ExecutionResult<string>> {
        const opts: SpawnOptions = { ...options };
        if (this.envVars) {
            opts.env = this.envVars;
        }
        return this.procService.exec(this.pythonPath, ['-m', moduleName, ...args], opts);
    }
}
