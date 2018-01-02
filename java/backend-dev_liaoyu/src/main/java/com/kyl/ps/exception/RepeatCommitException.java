package com.kyl.ps.exception;

public class RepeatCommitException extends Exception {
	/**
	 * 
	 */
	private static final long serialVersionUID = 2498102801468219645L;

	public RepeatCommitException() {
		super();
	}

	public RepeatCommitException(String message, Throwable cause) {
		super(message, cause);
	}

	public RepeatCommitException(String message) {
		super(message);
	}

	public RepeatCommitException(Throwable cause) {
		super(cause);
	}

}
