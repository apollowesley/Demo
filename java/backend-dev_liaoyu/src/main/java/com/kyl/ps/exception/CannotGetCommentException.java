package com.kyl.ps.exception;

public class CannotGetCommentException extends Exception {

	/** serialVersionUID*/
	private static final long serialVersionUID = 2005822079140637512L;

	public CannotGetCommentException() {
		super();
	}

	public CannotGetCommentException(String message, Throwable cause) {
		super(message, cause);
	}

	public CannotGetCommentException(String message) {
		super(message);
	}

	public CannotGetCommentException(Throwable cause) {
		super(cause);
	}


}

